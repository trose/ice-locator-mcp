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
  UpdateFieldLevelEncryptionProfileRequest,
  UpdateFieldLevelEncryptionProfileResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface UpdateFieldLevelEncryptionProfileCommandInput
  extends UpdateFieldLevelEncryptionProfileRequest {}
export interface UpdateFieldLevelEncryptionProfileCommandOutput
  extends UpdateFieldLevelEncryptionProfileResult,
    __MetadataBearer {}
export declare class UpdateFieldLevelEncryptionProfileCommand extends $Command<
  UpdateFieldLevelEncryptionProfileCommandInput,
  UpdateFieldLevelEncryptionProfileCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: UpdateFieldLevelEncryptionProfileCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: UpdateFieldLevelEncryptionProfileCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    UpdateFieldLevelEncryptionProfileCommandInput,
    UpdateFieldLevelEncryptionProfileCommandOutput
  >;
  private serialize;
  private deserialize;
}
