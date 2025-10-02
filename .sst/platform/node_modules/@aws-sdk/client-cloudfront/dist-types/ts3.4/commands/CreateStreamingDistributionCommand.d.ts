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
  CreateStreamingDistributionRequest,
  CreateStreamingDistributionResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface CreateStreamingDistributionCommandInput
  extends CreateStreamingDistributionRequest {}
export interface CreateStreamingDistributionCommandOutput
  extends CreateStreamingDistributionResult,
    __MetadataBearer {}
export declare class CreateStreamingDistributionCommand extends $Command<
  CreateStreamingDistributionCommandInput,
  CreateStreamingDistributionCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: CreateStreamingDistributionCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: CreateStreamingDistributionCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    CreateStreamingDistributionCommandInput,
    CreateStreamingDistributionCommandOutput
  >;
  private serialize;
  private deserialize;
}
