import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import { DeleteStreamingDistributionRequest } from "../models/models_1";
export { __MetadataBearer, $Command };
export interface DeleteStreamingDistributionCommandInput
  extends DeleteStreamingDistributionRequest {}
export interface DeleteStreamingDistributionCommandOutput
  extends __MetadataBearer {}
export declare class DeleteStreamingDistributionCommand extends $Command<
  DeleteStreamingDistributionCommandInput,
  DeleteStreamingDistributionCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: DeleteStreamingDistributionCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: DeleteStreamingDistributionCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    DeleteStreamingDistributionCommandInput,
    DeleteStreamingDistributionCommandOutput
  >;
  private serialize;
  private deserialize;
}
