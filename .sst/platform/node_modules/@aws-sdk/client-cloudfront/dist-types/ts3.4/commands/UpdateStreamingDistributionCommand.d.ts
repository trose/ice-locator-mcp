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
import {
  UpdateStreamingDistributionRequest,
  UpdateStreamingDistributionResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface UpdateStreamingDistributionCommandInput
  extends UpdateStreamingDistributionRequest {}
export interface UpdateStreamingDistributionCommandOutput
  extends UpdateStreamingDistributionResult,
    __MetadataBearer {}
export declare class UpdateStreamingDistributionCommand extends $Command<
  UpdateStreamingDistributionCommandInput,
  UpdateStreamingDistributionCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: UpdateStreamingDistributionCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: UpdateStreamingDistributionCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    UpdateStreamingDistributionCommandInput,
    UpdateStreamingDistributionCommandOutput
  >;
  private serialize;
  private deserialize;
}
